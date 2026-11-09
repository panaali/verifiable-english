import VE.Commands.Steps
import VE.SpeechActs.Run
import VE.Scope.Govern

/-! The one owner of command English (docs/spec/commands-imperatives.md section 6, CI-2): the reading context, the
proof task, `readInstruction` (the one public entry for this mode) and the `english.command` mode. Each sentence is
translated once: the proof task's sentence through `guardOf` inside the 400-byte bound, or a command condition
through `readCommand`; `many` holds
at most `readingsBound` readings (`manyOf`). -/

namespace VE.Commands

open Lean (Json toJson)
open VE.SpeechActs (Scope)
open VE.SpeechActs.Wire (SpeechEnvironment)
open VE.EnglishGrammar (Env Lexicon fillHoles)

/-- A decoded query record of the request (N7): its id and its target formula. -/
structure QueryRecord where
  id : String
  target : VE.Formula
  deriving DecidableEq, Repr

/-- The reading context of one command fence (A2). `b` is english-lean's `workBudget` (O7); no request sets it. -/
structure Context where
  se : SpeechEnvironment
  sc : Scope
  E : Env
  L : Lexicon
  b : Nat
  queries : List QueryRecord

/-- A proof task's sentence, between `Prove that ` and ` using these premises.`; `none` otherwise. -/
def proofSentence (s : String) : Option String :=
  let t := trimmed s
  if (prefixRefusal s).isNone && t.startsWith "Prove that " && t.endsWith " using these premises." then
    some ((t.drop "Prove that ".length).dropRight " using these premises.".length)
  else none

def ofPart (part text : String) : String := text.replace "The condition " (part ++ " ")

/-- The one record whose target is `φ`. -/
def matchedRecord (ctx : Context) (φ : VE.Formula) : Option QueryRecord :=
  match ctx.queries.filter (·.target == φ) with
  | [q] => some q
  | _ => none

/-- The obligation predicates with the proof task's act on `(…, query)`. -/
def proofPreds (ctx : Context) : List VE.Norms.Regulated :=
  ctx.se.ne.regulated.filter fun g => g.role == .obligation && g.act == some Texts.proofAct && g.sorts.drop 1 == ["query"]

def proofReading (g : VE.Norms.Regulated) (q : QueryRecord) : Reading := ⟨.require, g.name, [⟨q.id, q.id⟩], .top⟩

/-- O2 (reviews/dri-decisions-20261102-ci-0.md item 3): for an ambiguous sentence, one proof reading per reading that
is exactly one record's target, in the reader's order; fewer than two is `QueryMismatch`, never `one`. -/
def proofMany (ctx : Context) (gs : List VE.Formula) : Outcome :=
  match gs.filterMap (matchedRecord ctx) with
  | qs@(_ :: _ :: _) =>
    match proofPreds ctx with
    | [g] => manyOf (qs.map (proofReading g))
    | _ => .refused Texts.missingObligation Texts.proofAct
  | _ => .ofText Texts.queryMismatch

/-- The proof task (SA 2.1; N7), in the plan's order: over 400 bytes is `limit` before it is read (O10); P through
`guardOf` (budget `limit`, unread the reader's refusal said of "The sentence to prove", ambiguous `proofMany`);
exactly one record whose target is P's reading, else `QueryMismatch`; exactly one proof predicate, else
`MissingObligationRole`; then `checkedAddressee`. `none` when the wording is not a proof task. -/
def proofTask (ctx : Context) (s : String) : Option Outcome :=
  (proofSentence s).map fun p =>
    if maxWordingBytes < (trimmed s).utf8ByteSize then .limit
    else match guardOf ctx.se ctx.E ctx.L ctx.b p with
      | .error .limit => .limit
      | .error (.unread code text) => .refused code (ofPart "The sentence to prove" text)
      | .error (.ambiguous gs) => proofMany ctx gs
      | .ok φ =>
        match matchedRecord ctx φ with
        | some q =>
          match proofPreds ctx with
          | [g] => checkedAddressee ctx.se ctx.sc (proofReading g q)
          | _ => .refused Texts.missingObligation Texts.proofAct
        | none => .ofText Texts.queryMismatch

/-- The public entry for `english.command` (A3), through CI-3's step reader: a proof task's outcome is
`lift (.core s) false`, else `readStep`. Source-wrapper integration is deferred to ci-2b. -/
def readInstruction (ctx : Context) (s : String) : StepOutcome :=
  match proofTask ctx s with
  | some o => lift (.core s) false o
  | none => readStep ctx.se ctx.sc ctx.E ctx.L ctx.b s

/-! ## Steps and their stated order (section 7) -/

def stepCommands (u : String) (rs : List Reading) : List VE.SpeechActs.Command :=
  rs.mapIdx fun i r => r.command (u ++ "." ++ toString (i + 1))

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

/-- The request: `english.read`'s environment, overlay and lexicon, the speech environment and its scope, the
request's decoded query records, the command unit and the wording. -/
structure Request where
  id : String
  unit : String
  ctx : Context
  s : String

namespace Run

/-- `english.read`'s refusal row as one message. -/
def message (fs : List (String × Json)) : String := s!"{strField fs "code"}: {strField fs "text"}"

/-- The request `{id, environment, lexicon, unit, wording, queries, overlay?, generated?}`: a tree no parser builds
is refused first (`jsonWF?`); the environment is decoded by the speech decoder and by `english.read`'s, whose overlay
and lexicon refusals come before any wording is read; each query record names a declared `query` constant once. -/
def decodeRequest (j : Json) : Except String Request := do
  unless VE.Scope.jsonWF? j do throw "InvalidInput: the request is not a well-formed JSON tree"
  VE.Bridge.exactFields j (["id", "environment", "lexicon", "unit", "wording", "queries"] ++
    VE.EnglishGrammar.Run.optionalFields j)
  let id ← VE.Bridge.stringField j "id"
  let unit ← VE.Bridge.stringField j "unit"
  let s ← VE.Bridge.stringField j "wording"
  let se ← VE.SpeechActs.Wire.decodeSpeechEnvironmentFull (← j.getObjVal? "environment")
  let c ← VE.EnglishGrammar.Run.decodeCase j
  if let some f := c.overlayFailure then
    throw (message (VE.EnglishGrammar.Run.invalidOverlayFields "english.command" f))
  if let some g := VE.EnglishGrammar.grammarFault c.E {} c.L then
    throw (message (VE.EnglishGrammar.Run.invalidFields "english.command" c g))
  let qs ← (← (← j.getObjVal? "queries").getArr?).toList.mapM (VE.SpeechActs.Wire.decodeQuery se.ne.rv.environment)
  unless (qs.map (·.1)).eraseDups.length == qs.length do throw "InvalidInput: duplicate query"
  unless qs.all (fun q => se.ne.rv.vocabulary.constants.contains (q.1, "query")) do throw "InvalidInput: query"
  pure ⟨id, unit, ⟨se, se.scope, c.E, c.L, VE.EnglishGrammar.workBudget, qs.map fun (i, _, t) => ⟨i, t⟩⟩, s⟩

/-- The paraphrase's document: the context's environment, scope and regulated declarations. -/
def doc (ctx : Context) : VE.SpeechActs.SpeechDoc := ⟨ctx.se.ne.rv.environment, [], ctx.sc, ctx.se.ne.regulated, [], [], [], [], []⟩

/-- Where hole `{k}` starts in an act's phrase after `{0} `, the other holes filled. -/
def holeStart (act : String) (fs : List Fill) (k : Nat) : Nat :=
  (fillHoles (((act.drop 4).splitOn s!"\{{k}}").headD "") fun i => ((fs[i - 1]?).map (·.words)).getD "").2.length

/-- Where each step's command text starts in the trimmed wording, in code points: `shapes` cuts at `If <c>, `,
`Then ` and `, then `, and `capitalise` keeps the length. -/
def stepStarts : Shape → List Nat
  | .core _ => [0]
  | .preposed c _ => [c.length + 5]
  | .after _ => [5]
  | .seq xs => (xs.foldl (fun (acc, k) x => (acc ++ [k], k + x.length + 7)) ([], 0)).1

/-- A reading: its command object (SA 3.2), each fill with its span in code points of the wording (none for the
proof task's query, or when `start`, the start of the reading's command text, is not known), the proof task's query,
and speech-acts' paraphrase. -/
def readingJson (q : Request) (start : Option Nat) (r : Reading) : Json :=
  let act := ((q.ctx.se.ne.regulated.find? (·.name == r.act)).bind (·.act)).getD ""
  let base := (q.s.toList.takeWhile VE.SpeechActs.Wire.asciiSpace).length + if r.force = .forbid then 7 else 0
  let proof := (proofSentence q.s).isSome
  let span (f : Fill) (i : Nat) : Json :=
    match proof, start with
    | false, some k => VE.EnglishGrammar.Run.spanJson (base + k + holeStart act r.fills i,
        base + k + holeStart act r.fills i + f.words.length)
    | _, _ => .null
  Json.mkObj [("command", Json.mkObj [("force", VE.SpeechActs.Wire.encodeForce r.force), ("act", .str r.act),
      ("args", toJson (r.fills.map (·.const))), ("guard", VE.SpeechActs.Run.enc r.guard)]),
    ("fills", Json.arr ((r.fills.zipIdx 1).map fun (f, i) =>
      Json.mkObj [("constant", .str f.const), ("words", .str f.words), ("span", span f i)]).toArray),
    ("query", match proof, r.fills with
      | true, [f] => .str f.const
      | _, _ => .null),
    ("paraphrase", .str (VE.SpeechActs.Run.paraphrase (doc q.ctx) (r.command q.unit)))]

def shapeName : Shape → String
  | .core _ => "core"
  | .preposed _ _ => "preposed"
  | .after _ => "after"
  | .seq _ => "seq"

/-- An alternative of `many`: its shape's name and its readings, each with where its command text starts. -/
def altParts : Alt → String × List (Option Nat × Reading)
  | .shape sh rs => (shapeName sh, (rs.zip (stepStarts sh)).map fun (r, k) => (some k, r))
  | .form _ => ("form", [])
  | .purpose r _ => ("purpose", [(none, r)])

/-- Each alternative's shape and the positions of its readings in the answer's `readings`, from `k`. -/
def altIndexes : Nat → List (String × List (Option Nat × Reading)) → List Json
  | _, [] => []
  | k, (n, rs) :: rest =>
    Json.mkObj [("shape", .str n), ("readings", toJson (List.range' k rs.length))] :: altIndexes (k + rs.length) rest

/-- The one shape a single reading can come from (`Then <x>.` when `after`, else the merged or preposed wording),
when exactly one is possible. -/
def oneShape (s : String) (after : Bool) : Option Shape :=
  match (shapes s).filter (fun sh => match sh with
      | .after _ => after
      | .seq _ => false
      | _ => !after) with
  | [sh] => some sh
  | _ => none

def outcomeFields (q : Request) : StepOutcome → List (String × Json)
  | .one r a => [("outcome", .str "one"),
      ("reading", readingJson q ((oneShape q.s a).bind fun sh => (stepStarts sh).head?) r), ("after_previous", .bool a)]
  | .steps rs =>
    let ks := match (shapes q.s).find? (· matches .seq _) with
      | some sh => stepStarts sh
      | none => []
    [("outcome", .str "steps"),
      ("readings", Json.arr ((rs.zipIdx).map fun (r, i) => readingJson q ks[i]? r).toArray),
      ("paraphrase", .str (VE.SpeechActs.Run.paraphraseSteps (doc q.ctx) (stepCommands q.unit rs)))]
  | .many alts =>
    let ps := alts.map altParts
    [("outcome", .str "many"),
      ("readings", Json.arr ((ps.flatMap (·.2)).map fun (k, r) => readingJson q k r).toArray),
      ("alternatives", Json.arr (altIndexes 0 ps).toArray)]
  | .refused code text => [("outcome", .str "refused"), ("code", .str code), ("class", .str ((Texts.classOf code).getD "")),
      ("text", .str (if code == Texts.queryMismatch.1 then q.unit else text))]
  | .limit => [("outcome", .str "limit"), ("text", .str Texts.limitText)]
  | .mixed r p => [("outcome", .str "mixed"), ("reading", readingJson q none r), ("purpose", .str p)]

/-- The answer: the request's id and command unit, the wording, the scope's legend and the outcome's fields. -/
def encode (q : Request) (o : StepOutcome) : Json :=
  VE.Route.Wire.ok q.id [("result", Json.mkObj ([("unit", .str q.unit), ("wording", .str q.s),
    ("legend", toJson (VE.SpeechActs.Run.legend q.ctx.sc))] ++ outcomeFields q o))]

def caseReported (j : Json) : Json :=
  match decodeRequest j with
  | .ok q => encode q (readInstruction q.ctx q.s)
  | .error e => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str e)]

end Run

/-! ## The statements (section 6) -/

section Statements

-- `readInstruction` now returns `StepOutcome`: a proof task's outcome is `lift (.core s) false`, else `readStep`.
theorem readInstruction_step (ctx : Context) (s : String) (h : proofTask ctx s = none) :
    readInstruction ctx s = readStep ctx.se ctx.sc ctx.E ctx.L ctx.b s := by  -- replaces `readInstruction_command`
  simp [readInstruction, h]

theorem caseReported_eq (j : Json) (q : Request) (hd : Run.decodeRequest j = .ok q) :
    Run.caseReported j = Run.encode q (readInstruction q.ctx q.s) := by
  simp [Run.caseReported, hd]

theorem proofMany_one (ctx : Context) (gs : List VE.Formula) (r : Reading) : proofMany ctx gs ≠ .one r := by
  unfold proofMany
  split
  · split
    · exact manyOf_one _ r
    · simp
  · simp [Outcome.ofText]

/-- A proof task's single reading: its sentence's one guard, the one record with that target, the one proof
predicate, and an addressed reading of it. -/
theorem proofTask_one (ctx : Context) (s : String) (r : Reading) (h : proofTask ctx s = some (.one r)) :
    ∃ p φ q g, proofSentence s = some p ∧ guardOf ctx.se ctx.E ctx.L ctx.b p = .ok φ ∧
      ctx.queries.filter (·.target == φ) = [q] ∧ proofPreds ctx = [g] ∧ r = proofReading g q ∧
      addressed ctx.se ctx.sc r = true := by
  unfold proofTask at h
  cases hp : proofSentence s with
  | none => simp [hp] at h
  | some p =>
    simp only [hp, Option.map_some, Option.some.injEq] at h
    split at h
    · cases h
    · split at h
      · cases h
      · cases h
      · exact absurd h (proofMany_one ctx _ r)
      · rename_i φ hg
        cases hm : matchedRecord ctx φ with
        | none => simp [hm, Outcome.ofText] at h
        | some q =>
          simp only [hm] at h
          split at h
          · rename_i g hpp
            obtain ⟨rfl, ha⟩ := (checked_one ctx.se ctx.sc _ _).mp h
            refine ⟨p, φ, q, g, rfl, hg, ?_, hpp, rfl, ha⟩
            unfold matchedRecord at hm
            split at hm
            · cases hm; assumption
            · cases hm
          · cases h

/-- The proof task names the one query record whose target is P's reading (N7). -/
theorem proofTask_bound (ctx : Context) (s p : String) (r : Reading) (hp : proofSentence s = some p)
    (h : proofTask ctx s = some (.one r)) :
    ∃ φ q, guardOf ctx.se ctx.E ctx.L ctx.b p = .ok φ ∧ ctx.queries.filter (·.target == φ) = [q] ∧
      r.fills.map (·.const) = [q.id] := by
  obtain ⟨p', φ, q, g, hp', hg, hq, _, rfl, _⟩ := proofTask_one ctx s r h
  rw [hp] at hp'
  cases hp'
  exact ⟨φ, q, hg, hq, rfl⟩

theorem proofTask_addressed (ctx : Context) (s : String) (r : Reading)
    (h : proofTask ctx s = some (.one r)) : addressed ctx.se ctx.sc r = true := by
  obtain ⟨_, _, _, _, _, _, _, _, _, ha⟩ := proofTask_one ctx s r h
  exact ha

/-- A proof task's refusal is classed: english-lean's refusal of the sentence (`guardOf_classed`) or the reader's. -/
theorem proofTask_refused_classed (ctx : Context) (s code text : String)
    (ht : proofTask ctx s = some (.refused code text)) : (Texts.classOf code).isSome = true := by
  unfold proofTask at ht
  cases hp : proofSentence s with
  | none => simp [hp] at ht
  | some p =>
    simp only [hp, Option.map_some, Option.some.injEq] at ht
    split at ht
    · cases ht
    · split at ht
      · cases ht
      · cases ht; exact guardOf_classed ctx.se ctx.E ctx.L ctx.b p code _ ‹_›
      · unfold proofMany at ht
        split at ht
        · split at ht
          · unfold manyOf at ht; split at ht <;> cases ht
          · cases ht; rfl
        · cases ht; rfl
      · split at ht
        · split at ht
          · unfold checkedAddressee Outcome.ofText at ht
            split at ht
            · cases ht
            · split at ht <;> (cases ht; rfl)
          · cases ht; rfl
        · cases ht; rfl

theorem lift_refused {sh : Shape} {a : Bool} {o : Outcome} {c t : String} :
    lift sh a o = .refused c t ↔ o = .refused c t := by
  cases o <;> simp [lift]

theorem lift_steps {sh : Shape} {a : Bool} {o : Outcome} {rs : List Reading} : lift sh a o ≠ .steps rs := by
  cases o <;> simp [lift]

variable {se : SpeechEnvironment} {sc : Scope} {E : Env} {L : Lexicon} {b : Nat}

/-- A sequence's first fault: a step's own refusal, or `ConditionScope`. -/
theorem seqFault_classed {xs : List String} {f : StepOutcome} {c t : String}
    (h : (xs.map fun x => readCommand se sc E L b (capitalise x ++ ".")).findSome? (fun o => match o with
      | .refused code text => some (.refused code text)
      | .one r => if r.guard == .top then none else some conditionScope
      | .many rs => if rs.any (·.guard != .top) then some conditionScope else none
      | .limit => none) = some f) (hf : f = .refused c t) : (Texts.classOf c).isSome = true := by
  obtain ⟨o, hm, ho⟩ := List.exists_of_findSome?_eq_some h
  obtain ⟨x, _, rfl⟩ := List.mem_map.1 hm
  subst hf
  revert ho
  cases hr : readCommand se sc E L b (capitalise x ++ ".") with
  | refused c' t' =>
    intro ho; cases ho; exact refused_classed se sc E L b _ c t hr
  | one r => intro ho; simp only at ho; split at ho <;> cases ho; rfl
  | many rs => intro ho; simp only at ho; split at ho <;> cases ho; rfl
  | limit => intro ho; cases ho

theorem shapeOutcome_refused_classed {sh : Shape} {c t : String} (h : shapeOutcome se sc E L b sh = .refused c t) :
    (Texts.classOf c).isSome = true := by
  cases sh with
  | core => exact refused_classed se sc E L b _ c t (lift_refused.1 h)
  | after => exact refused_classed se sc E L b _ c t (lift_refused.1 h)
  | preposed =>
    simp only [shapeOutcome] at h
    split at h
    · simp only [conditionScope, StepOutcome.refused.injEq] at h; obtain ⟨rfl, _⟩ := h; rfl
    · exact refused_classed se sc E L b _ c t (lift_refused.1 h)
  | seq xs =>
    simp only [shapeOutcome] at h
    split at h
    · exact seqFault_classed ‹_› h
    · split at h
      · cases h
      split at h
      · cases h
      split at h
      · cases h
      · simp only [StepOutcome.refused.injEq] at h; obtain ⟨rfl, _⟩ := h; rfl
      · split at h <;> cases h

theorem combine_refused_classed {os : List (Shape × StepOutcome)} {c t : String}
    (h : combineShapes os = .refused c t) : (Texts.classOf c).isSome = true := by
  simp only [combineShapes] at h
  split at h
  · simp at h
  split at h
  · simp at h
  split at h
  · simp at h
  split at h
  · rename_i o ho
    subst h
    obtain ⟨⟨_, o'⟩, _, hp⟩ := List.exists_of_findSome?_eq_some ho
    cases o' <;> simp at hp
  · split at h
    · simp only [conditionScope, StepOutcome.refused.injEq] at h; obtain ⟨rfl, _⟩ := h; rfl
    · simp only [StepOutcome.refused.injEq] at h; obtain ⟨rfl, _⟩ := h; rfl

/-- `readStep`'s outcome is a shape's own outcome, `limit`, or the combination of every shape's outcome. -/
theorem readStep_from {s : String} {o : StepOutcome} (h : readStep se sc E L b s = o) :
    o = .limit ∨ (∃ sh ∈ shapes s, shapeOutcome se sc E L b sh = o) ∨
      combineShapes ((shapes s).map fun sh => (sh, shapeOutcome se sc E L b sh)) = o := by
  rcases Nat.lt_or_ge maxWordingBytes (trimmed s).utf8ByteSize with hb | hb
  · exact .inl (h.symm.trans (readStep_over se sc E L b s hb))
  · by_cases hs : ∃ sh, shapes s = [sh]
    · obtain ⟨sh, hs⟩ := hs
      exact .inr (.inl ⟨sh, by simp [hs], (readStep_one se sc E L b s hb hs).symm.trans h⟩)
    · exact .inr (.inr ((readStep_combine se sc E L b s hb fun sh h' => hs ⟨sh, h'⟩).symm.trans h))

/-- The CI-3 public entry has a class for every step and condition refusal. -/
theorem readInstruction_refused_classed_step (ctx : Context) (s code text : String)
    (h : readInstruction ctx s = StepOutcome.refused code text) : (Texts.classOf code).isSome = true := by
  unfold readInstruction at h
  cases ht : proofTask ctx s with
  | some o =>
    rw [ht] at h
    exact proofTask_refused_classed ctx s code text (ht.trans (congrArg some (lift_refused.1 h)))
  | none =>
    rw [ht] at h
    rcases readStep_from h with h | ⟨sh, _, h⟩ | h
    · cases h
    · exact shapeOutcome_refused_classed h
    · exact combine_refused_classed h

/-- ci-2's form (reviews/dri-decisions-20261104-ci-2.md item 1), now a corollary: ci-1b's two facts are on main. -/
theorem readInstruction_refused_classed_of (ctx : Context) (s code text : String)
    (_hc : ∀ c t, readCommand ctx.se ctx.sc ctx.E ctx.L ctx.b s = .refused c t → (Texts.classOf c).isSome = true)
    (_hg : ∀ p c t, guardOf ctx.se ctx.E ctx.L ctx.b p = .error (.unread c t) → (Texts.classOf c).isSome = true)
    (h : readInstruction ctx s = .refused code text) : (Texts.classOf code).isSome = true :=
  readInstruction_refused_classed_step ctx s code text h

/-- A proof task's single reading passes the semantic core's check, given the `declared` facts. -/
theorem proofTask_typed_of_facts (ctx : Context) (s : String) (r : Reading) (D : VE.SpeechActs.SpeechDoc)
    (u : String) (hf : declared ctx.se = true) (ht : proofTask ctx s = some (.one r))
    (hE : D.E = ctx.se.ne.rv.environment) (hS : D.scope = ctx.sc) (hR : D.regulated = ctx.se.ne.regulated)
    (hk : VE.SpeechActs.scopeOk D = true)
    (hq : ∀ q ∈ ctx.queries, (q.id, "query") ∈ ctx.se.ne.rv.vocabulary.constants) :
    VE.SpeechActs.commandOk D (r.command u) = true := by
  obtain ⟨_, φ, q, g, _, _, hfq, hpp, rfl, ha⟩ := proofTask_one ctx s r ht
  have hgm : g ∈ proofPreds ctx := by simp [hpp]
  simp only [proofPreds, List.mem_filter, Bool.and_eq_true, beq_iff_eq] at hgm
  obtain ⟨hmem, ⟨hrole, _⟩, hsorts⟩ := hgm
  have hqm : q ∈ ctx.queries := (List.mem_filter.mp (hfq ▸ List.mem_singleton_self q)).1
  simp only [declared, Bool.and_eq_true, List.all_eq_true, beq_iff_eq] at hf
  obtain ⟨hreg, hcon⟩ := hf
  have hfind := (hreg g hmem).2
  simp only [addressed, proofReading, hfind] at ha
  cases hadr : ctx.sc.addressee with
  | none => simp [hadr] at ha
  | some x =>
    obtain ⟨srt, you⟩ := x
    have hyou : D.E.constants you = some srt := by
      simp only [VE.SpeechActs.scopeOk, hS, hadr, Bool.and_eq_true, beq_iff_eq] at hk
      exact hk.1.1.1.2.2
    cases hs : g.sorts with
    | nil => simp [hadr, hs] at ha
    | cons s0 rest =>
      have h0 : s0 = srt := by simpa [hadr, hs] using ha
      have hrest : rest = ["query"] := by simpa [hs] using hsorts
      subst h0 hrest
      simp only [VE.SpeechActs.commandOk, VE.SpeechActs.regOf, hR, Reading.command, proofReading, hfind, hS, hadr]
      simp [hE ▸ hyou, hE, (hreg g hmem).1, hs, hrole, VE.SpeechActs.constsTyped, hcon _ (hq q hqm),
        VE.Formula.check]

/-- A shape's single reading is a `readCommand` `one`. -/
theorem shapeOutcome_one {sh : Shape} {r : Reading} {a : Bool} (h : shapeOutcome se sc E L b sh = .one r a) :
    ∃ w, readCommand se sc E L b w = .one r := by
  cases sh with
  | core => exact ⟨_, (lift_one.1 h).1⟩
  | after => exact ⟨_, (lift_one.1 h).1⟩
  | preposed =>
    simp only [shapeOutcome] at h
    split at h
    · cases h
    · exact ⟨_, (lift_one.1 h).1⟩
  | seq xs =>
    simp only [shapeOutcome] at h
    split at h
    · obtain ⟨_, _, rfl⟩ := seqFault ‹_›
      cases h
    · split at h
      · cases h
      split at h
      · cases h
      split at h
      · cases h
      · cases h
      · split at h <;> cases h

theorem exists_mem_zip_right {α β : Type} : ∀ {l : List α} {m : List β}, l.length = m.length → ∀ y ∈ m,
    ∃ x, (x, y) ∈ l.zip m
  | _, [], _, _, h => by simp at h
  | [], _ :: _, hl, _, _ => by simp at hl
  | a :: l, c :: m, hl, y, hy => by
    simp only [List.length_cons, Nat.add_right_cancel_iff, List.mem_cons] at hl hy
    rcases hy with rfl | hy
    · exact ⟨a, by simp⟩
    · obtain ⟨x, hx⟩ := exists_mem_zip_right hl y hy
      exact ⟨x, by simp [hx]⟩

/-- Each step of a read sequence is a `readCommand` `one` (`many` has at least two readings). -/
theorem shapeOutcome_steps {sh : Shape} {rs : List Reading} (h : shapeOutcome se sc E L b sh = .steps rs) :
    ∀ r ∈ rs, ∃ w, readCommand se sc E L b w = .one r := by
  cases sh with
  | core => exact absurd h lift_steps
  | after => exact absurd h lift_steps
  | preposed =>
    simp only [shapeOutcome] at h
    split at h
    · cases h
    · exact absurd h lift_steps
  | seq xs =>
    simp only [shapeOutcome] at h
    split at h
    · obtain ⟨_, _, rfl⟩ := seqFault ‹_›
      cases h
    split at h
    · cases h
    split at h
    · cases h
    split at h
    · rename_i rs' hall
      simp only [StepOutcome.steps.injEq] at h
      subst h
      rw [List.map_map] at hall
      obtain ⟨h1, h2⟩ := (readingTuples_single _ xs rs').1 hall
      intro r hr
      obtain ⟨x, hz⟩ := exists_mem_zip_right h1 r hr
      have hc := h2 (x, r) hz
      simp only [Function.comp] at hc
      revert hc
      cases hf : readCommand se sc E L b (capitalise x ++ ".") with
      | one r' => intro hc; simp only [List.cons.injEq, and_true] at hc; exact ⟨_, hc ▸ hf⟩
      | many rs'' =>
        have := ((readCommand_many se sc E L b _ rs'').1 hf).2.2.1
        intro hc; subst hc; simp at this
      | _ => simp
    · cases h
    · split at h <;> cases h

/-- `combineShapes` yields `one` or `steps` only as one shape's own outcome. -/
theorem combine_from {os : List (Shape × StepOutcome)} {o : StepOutcome} (h : combineShapes os = o)
    (hl : o ≠ .limit) (hm : ∀ a, o ≠ .many a) (hn : ∀ c t, o ≠ .refused c t) : ∃ p ∈ os, p.2 = o := by
  simp only [combineShapes] at h
  split at h
  · exact absurd h.symm hl
  split at h
  · exact absurd h.symm (hm _)
  split at h
  · exact absurd h.symm hl
  split at h
  · rename_i o' ho
    subst h
    obtain ⟨⟨sh, o''⟩, hp, hs⟩ := List.exists_of_findSome?_eq_some ho
    refine ⟨(sh, o''), hp, ?_⟩
    cases o'' <;> simp at hs <;> exact hs
  · split at h
    · exact absurd h.symm (hn _ _)
    · exact absurd h.symm (hn _ _)

/-- Every reading of a `one` or a `steps` of `readStep` is a `readCommand` `one`. -/
theorem readStep_read {s : String} {r : Reading}
    (h : (∃ x, readStep se sc E L b s = .one r x) ∨ ∃ rs, readStep se sc E L b s = .steps rs ∧ r ∈ rs) :
    ∃ w, readCommand se sc E L b w = .one r := by
  have key : ∀ o, readStep se sc E L b s = o → o ≠ .limit → (∀ a, o ≠ .many a) → (∀ c t, o ≠ .refused c t) →
      ∃ sh, shapeOutcome se sc E L b sh = o := fun o ho hl hm hn => by
    rcases readStep_from ho with h | ⟨sh, _, h⟩ | h
    · exact absurd h hl
    · exact ⟨sh, h⟩
    · obtain ⟨p, hp, hp2⟩ := combine_from h hl hm hn
      obtain ⟨sh, _, rfl⟩ := List.mem_map.1 hp
      exact ⟨sh, hp2⟩
  rcases h with ⟨x, hx⟩ | ⟨rs, hrs, hr⟩
  · obtain ⟨sh, hsh⟩ := key _ hx (by simp) (by simp) (by simp)
    exact shapeOutcome_one hsh
  · obtain ⟨sh, hsh⟩ := key _ hrs (by simp) (by simp) (by simp)
    exact shapeOutcome_steps hsh r hr

/-- The typing theorem over the whole entry, the proof task included (N7), given the `declared` facts of
`readCommand_typed_of_facts`: a `one`, and every member of `steps`. -/
theorem readInstruction_typed_of_facts (ctx : Context) (s : String) (r : Reading) (D : VE.SpeechActs.SpeechDoc)
    (u : String) (hf : declared ctx.se = true)
    (h : (∃ x, readInstruction ctx s = StepOutcome.one r x) ∨
      ∃ rs, readInstruction ctx s = StepOutcome.steps rs ∧ r ∈ rs)
    (hE : D.E = ctx.se.ne.rv.environment) (hS : D.scope = ctx.sc) (hR : D.regulated = ctx.se.ne.regulated)
    (hk : VE.SpeechActs.scopeOk D = true)
    (hq : ∀ q ∈ ctx.queries, (q.id, "query") ∈ ctx.se.ne.rv.vocabulary.constants) :
    VE.SpeechActs.commandOk D (r.command u) = true := by
  unfold readInstruction at h
  cases ht : proofTask ctx s with
  | some o =>
    rw [ht] at h
    rcases h with ⟨x, hx⟩ | ⟨rs, hrs, _⟩
    · exact proofTask_typed_of_facts ctx s r D u hf (ht.trans (congrArg some (lift_one.1 hx).1)) hE hS hR hk hq
    · exact absurd hrs lift_steps
  | none =>
    rw [ht] at h
    obtain ⟨w, hw⟩ := readStep_read h
    exact readCommand_typed_of_facts ctx.se ctx.sc ctx.E ctx.L ctx.b w r D u hf hw hE hS hR hk

section
variable {s : String}

/-- `readInstruction_typed` through CI-3's entry (N7: the typing theorem covers every later batch): a `one`, and
every member of `steps`. It holds because each `one` and each `steps` member is a `readCommand` `one` (`many` has at
least two readings), and `commandOk` ignores the unit. `hw` is ci-1's (reviews/dri-decisions-20261102-ci-1.md item 1). -/
theorem readInstruction_typed_step (j : Lean.Json) (ctx : Context) (r : Reading) (D : VE.SpeechActs.SpeechDoc)
    (u : String) (hw : VE.Scope.JsonWF j) (hd : VE.SpeechActs.Wire.decodeSpeechEnvironmentFull j = .ok ctx.se)
    (h : (∃ x, readInstruction ctx s = StepOutcome.one r x) ∨
      ∃ rs, readInstruction ctx s = StepOutcome.steps rs ∧ r ∈ rs)
    (hE : D.E = ctx.se.ne.rv.environment) (hS : D.scope = ctx.sc) (hR : D.regulated = ctx.se.ne.regulated)
    (hk : VE.SpeechActs.scopeOk D = true)
    (hq : ∀ q ∈ ctx.queries, (q.id, "query") ∈ ctx.se.ne.rv.vocabulary.constants) :
    VE.SpeechActs.commandOk D (r.command u) = true :=
  readInstruction_typed_of_facts ctx s r D u (declared_of_decode hw hd) h hE hS hR hk hq

end

/-- A sequence contributes exactly its steps' demands, named `cmd-<u>.1` … `cmd-<u>.n`, and no other rule. -/
theorem stepCommands_policy (D : VE.SpeechActs.SpeechDoc) (u : String) (rs : List Reading)
    (pre post : List VE.SpeechActs.Command) (h : D.commands = pre ++ stepCommands u rs ++ post) :
    (VE.SpeechActs.policy D).T.nodes =
      D.norms ++ (pre ++ stepCommands u rs ++ post).map (VE.SpeechActs.demand D) := by
  simp [VE.SpeechActs.policy, h]

end Statements

end VE.Commands
