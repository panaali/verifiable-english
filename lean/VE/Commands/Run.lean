import VE.Commands.Read
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

/-- The public entry for `english.command` (A3). Source-wrapper integration is deferred to ci-2b. -/
def readInstruction (ctx : Context) (s : String) : Outcome :=
  (proofTask ctx s).getD (readCommand ctx.se ctx.sc ctx.E ctx.L ctx.b s)

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

/-- A reading: its command object (SA 3.2), each fill with its span in code points of the wording (none for the
proof task's query), the proof task's query, and speech-acts' paraphrase. -/
def readingJson (q : Request) (r : Reading) : Json :=
  let act := ((q.ctx.se.ne.regulated.find? (·.name == r.act)).bind (·.act)).getD ""
  let base := (q.s.toList.takeWhile VE.SpeechActs.Wire.asciiSpace).length + if r.force = .forbid then 7 else 0
  let proof := (proofSentence q.s).isSome
  let span (f : Fill) (i : Nat) : Json :=
    if proof then .null else VE.EnglishGrammar.Run.spanJson (base + holeStart act r.fills i, base + holeStart act r.fills i + f.words.length)
  Json.mkObj [("command", Json.mkObj [("force", VE.SpeechActs.Wire.encodeForce r.force), ("act", .str r.act),
      ("args", toJson (r.fills.map (·.const))), ("guard", VE.SpeechActs.Run.enc r.guard)]),
    ("fills", Json.arr ((r.fills.zipIdx 1).map fun (f, i) =>
      Json.mkObj [("constant", .str f.const), ("words", .str f.words), ("span", span f i)]).toArray),
    ("query", match proof, r.fills with
      | true, [f] => .str f.const
      | _, _ => .null),
    ("paraphrase", .str (VE.SpeechActs.Run.paraphrase (doc q.ctx) (r.command q.unit)))]

def outcomeFields (q : Request) : Outcome → List (String × Json)
  | .one r => [("outcome", .str "one"), ("reading", readingJson q r)]
  | .many rs => [("outcome", .str "many"), ("readings", Json.arr (rs.map (readingJson q)).toArray)]
  | .refused code text => [("outcome", .str "refused"), ("code", .str code), ("class", .str ((Texts.classOf code).getD "")),
      ("text", .str (if code == Texts.queryMismatch.1 then q.unit else text))]
  | .limit => [("outcome", .str "limit"), ("text", .str Texts.limitText)]

/-- The answer: the request's id and command unit, the wording, the scope's legend and the outcome's fields. -/
def encode (q : Request) (o : Outcome) : Json :=
  VE.Route.Wire.ok q.id [("result", Json.mkObj ([("unit", .str q.unit), ("wording", .str q.s),
    ("legend", toJson (VE.SpeechActs.Run.legend q.ctx.sc))] ++ outcomeFields q o))]

def caseReported (j : Json) : Json :=
  match decodeRequest j with
  | .ok q => encode q (readInstruction q.ctx q.s)
  | .error e => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str e)]

end Run

/-! ## The statements (section 6) -/

section Statements

theorem readInstruction_command (ctx : Context) (s : String) (h : proofTask ctx s = none) :
    readInstruction ctx s = readCommand ctx.se ctx.sc ctx.E ctx.L ctx.b s := by
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

/-- Every refusal of the entry is classed, given ci-1b's two facts: the reader's refusals are classed
(`refused_classed`) and so is english-lean's refusal of a sentence (`guardOf_classed`). -/
theorem readInstruction_refused_classed_of (ctx : Context) (s code text : String)
    (hc : ∀ c t, readCommand ctx.se ctx.sc ctx.E ctx.L ctx.b s = .refused c t → (Texts.classOf c).isSome = true)
    (hg : ∀ p c t, guardOf ctx.se ctx.E ctx.L ctx.b p = .error (.unread c t) → (Texts.classOf c).isSome = true)
    (h : readInstruction ctx s = .refused code text) : (Texts.classOf code).isSome = true := by
  unfold readInstruction at h
  cases ht : proofTask ctx s with
  | none => exact hc code text (by simpa [ht] using h)
  | some o =>
    simp only [ht, Option.getD_some] at h
    subst h
    unfold proofTask at ht
    cases hp : proofSentence s with
    | none => simp [hp] at ht
    | some p =>
      simp only [hp, Option.map_some, Option.some.injEq] at ht
      split at ht
      · cases ht
      · split at ht
        · cases ht
        · cases ht; exact hg p code _ ‹_›
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

/-- The typing theorem over the whole entry, the proof task included (N7), given the `declared` facts of
`readCommand_typed_of_facts` (ci-1b proves them of a decoded `JsonWF` environment) and `hq`. -/
theorem readInstruction_typed_of_facts (ctx : Context) (s : String) (r : Reading) (D : VE.SpeechActs.SpeechDoc)
    (u : String) (hf : declared ctx.se = true) (h : readInstruction ctx s = .one r)
    (hE : D.E = ctx.se.ne.rv.environment) (hS : D.scope = ctx.sc) (hR : D.regulated = ctx.se.ne.regulated)
    (hk : VE.SpeechActs.scopeOk D = true)
    (hq : ∀ q ∈ ctx.queries, (q.id, "query") ∈ ctx.se.ne.rv.vocabulary.constants) :
    VE.SpeechActs.commandOk D (r.command u) = true := by
  unfold readInstruction at h
  cases ht : proofTask ctx s with
  | none =>
    exact readCommand_typed_of_facts ctx.se ctx.sc ctx.E ctx.L ctx.b s r D u hf (by simpa [ht] using h) hE hS hR hk
  | some o =>
    simp only [ht, Option.getD_some] at h
    subst h
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

end Statements

end VE.Commands
